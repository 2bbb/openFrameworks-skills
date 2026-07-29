# openFrameworks runtime, resources, and ownership

Use this reference when an oF app loads assets, moves work off the main thread, receives live frames, owns listeners, updates GPU resources, controls timing, or composes multiple render passes.

## Contents

- [Data paths and runtime assets](#data-paths-and-runtime-assets)
- [CPU and GPU resource boundaries](#cpu-and-gpu-resource-boundaries)
- [Threads and frame handoff](#threads-and-frame-handoff)
- [Event listener lifetime](#event-listener-lifetime)
- [Frame timing and vertical sync](#frame-timing-and-vertical-sync)
- [Streaming video lifecycle](#streaming-video-lifecycle)
- [Render-state isolation](#render-state-isolation)
- [Agent checklist](#agent-checklist)

## Data paths and runtime assets

oF's data-path layer is enabled by default:

- `ofEnableDataPath()` makes `ofToDataPath()` respect the configured data root and is the default state.
- `ofDisableDataPath()` makes `ofToDataPath()` ignore that root.
- `ofToDataPathFS(path, absolute)` and `ofToDataPath(path, absolute)` resolve a path against the data directory; pass `true` when a non-oF API needs an absolute path.
- `ofSetDataPathRoot(root)` changes the data root. The checked source warns that the supplied root must end with `/`.

Source: `openFrameworks/libs/openFrameworks/utils/ofFileUtils.h`.

Practical rules:

1. Put ordinary runtime assets in the project's `bin/data` tree and pass relative paths such as `"shaders/post"` or `"images/logo.png"` to oF loaders.
2. Do not manually prepend `bin/data/` to every oF load call. Core image, sound, XML, font, and file implementations use the data-path layer in the inspected source. `ofVideoPlayer` delegates path handling to its selected backend, so verify that backend on the target platform/version.
3. Convert to an absolute path at the integration boundary:

   ```cpp
   const auto modelPath = ofToDataPathFS("models/scene.glb", true);
   thirdPartyLoader.open(modelPath);
   ```

4. Use `bRelativeToData = false`, `ofDisableDataPath()`, or a custom root only for an intentional external-path workflow. Do not globally disable data paths to fix one incorrectly specified asset.
5. Set a custom data root before loading dependent resources, and keep the root's trailing slash requirement in mind for the target oF version.
6. Avoid changing the process working directory as asset management. `ofRestoreWorkingDirectoryToDefault()` exists because platform/window layers may alter it; data-path APIs are the portable boundary.

Sources: `openFrameworks/libs/openFrameworks/utils/ofFileUtils.h`, `openFrameworks/libs/openFrameworks/utils/ofFileUtils.cpp`, `openFrameworks/libs/openFrameworks/graphics/ofImage.cpp`, `openFrameworks/libs/openFrameworks/video/ofVideoPlayer.cpp`, `openFrameworks/libs/openFrameworks/video/ofAVFoundationPlayer.mm`, `openFrameworks/libs/openFrameworks/video/ofGstVideoPlayer.cpp`, `openFrameworks/libs/openFrameworks/video/ofDirectShowPlayer.cpp`, `openFrameworks/libs/openFrameworks/video/ofMediaFoundationPlayer.cpp`, `openFrameworks/libs/openFrameworks/sound/ofFmodSoundPlayer.cpp`, `openFrameworks/libs/openFrameworks/sound/ofOpenALSoundPlayer.cpp`, `openFrameworks/libs/openFrameworks/utils/ofXml.cpp`, `openFrameworks/libs/openFrameworks/graphics/ofTrueTypeFont.cpp`.

When diagnosing a missing file, log both the requested relative path and `ofToDataPathFS(path, true)`, then check existence with `ofFile`/`of::filesystem` instead of guessing the launch directory.

## CPU and GPU resource boundaries

Keep this mental model:

- `ofPixels`, `ofShortPixels`, and `ofFloatPixels` are CPU-side pixel containers.
- `ofTexture` is an OpenGL texture. Size/format `allocate()` overloads create storage; `allocate(pixels)` allocates and performs the initial upload; `loadData()` updates an allocation with pixel data; `isAllocated()` gates safe use; `clear()` releases its allocation; and `readToPixels()` transfers texture data back into CPU pixels.
- `ofImage` owns pixels and can own a texture. If pixels are changed directly, call `ofImage::update()` before drawing so the texture reflects those pixels.
- `ofImage::setUseTexture(false)` allows image loading/processing without creating or updating the texture; re-enable texture use and call `update()` on the graphics thread when the result is ready.

Sources: `openFrameworks/libs/openFrameworks/graphics/ofPixels.h`, `openFrameworks/libs/openFrameworks/gl/ofTexture.h`, `openFrameworks/libs/openFrameworks/graphics/ofImage.h`.

Allocation is part of resource lifecycle, not a per-frame default:

```cpp
if (!texture.isAllocated()
    || texture.getWidth() != pixels.getWidth()
    || texture.getHeight() != pixels.getHeight()) {
    texture.allocate(pixels);
} else {
    texture.loadData(pixels);
}
```

Also compare pixel/internal formats when a stream can change format. The `allocate(pixels)` branch already uploads that first frame, so do not immediately upload it a second time. `ofVideoPlayer::update()` demonstrates reallocating when size or format changes; `ofVideoGrabber::update()` similarly allocates before later uploads. Sources: `openFrameworks/libs/openFrameworks/gl/ofTexture.cpp`, `openFrameworks/libs/openFrameworks/video/ofVideoPlayer.cpp`, `openFrameworks/libs/openFrameworks/video/ofVideoGrabber.cpp`.

Do not assume CPU and GPU copies remain synchronized automatically:

- Direct `ofImage` pixel edits require `update()`.
- Direct texture edits do not automatically update the image's CPU pixels.
- `ofTexture::readToPixels()` is explicitly a GPU-to-pixels operation and is not supported by that API on OpenGL ES.

Source: `openFrameworks/libs/openFrameworks/graphics/ofImage.h`, `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.

## Threads and frame handoff

`ofThread` explicitly states that OpenGL can run only in the main execution thread in the supported oF threading model. A safe default is:

1. Capture, decode, load, or analyze CPU data in a worker.
2. Send completed CPU objects to the main thread.
3. Drain results from `ofApp::update()` or another main-thread update listener.
4. Allocate/upload `ofTexture`, update textured `ofImage`, and draw only there.

Sources: `openFrameworks/libs/openFrameworks/utils/ofThread.h`, `openFrameworks/examples/threads/threadChannelExample/src/ImgAnalysisThread.cpp`, `openFrameworks/addons/ofxThreadedImageLoader/src/ofxThreadedImageLoader.cpp`.

### Prefer ownership transfer over shared mutable state

`ofThreadChannel<T>` is a one-way, thread-safe FIFO:

- `receive()` blocks until data arrives or the channel closes.
- `tryReceive()` is non-blocking.
- `send(const T&)` copies.
- `send(T&&)` moves.
- `close()` wakes blocked receivers; future receive/send operations report failure.

Source: `openFrameworks/libs/openFrameworks/utils/ofThreadChannel.h`.

For live sources, bounded latency usually matters more than processing every stale frame. The bundled `threadChannelExample` drains all available results with `tryReceive()` and keeps only the newest before uploading its texture:

```cpp
bool hasNew = false;
while (analyzed.tryReceive(pixels)) {
    hasNew = true;
}
if (hasNew) {
    if (!texture.isAllocated()
        || texture.getWidth() != pixels.getWidth()
        || texture.getHeight() != pixels.getHeight()) {
        texture.allocate(pixels);
    } else {
        texture.loadData(pixels);
    }
}
```

This adapts the example's drain-to-latest policy while avoiding a duplicate upload after `allocate(pixels)`. Sources: `openFrameworks/examples/threads/threadChannelExample/src/ImgAnalysisThread.cpp`, `openFrameworks/libs/openFrameworks/gl/ofTexture.cpp`.

Use that latest-frame policy only when dropping intermediate frames is acceptable. For recording, encoding, or transactional work, define a bounded queue/backpressure or loss policy explicitly rather than silently discarding data.

### Shutdown order is part of correctness

`stopThread()` only sets a flag; it does not forcibly terminate the worker. With the default infinite timeout, `waitForThread(true)` requests stop and waits for completion when called from outside the worker; a finite timeout can return before completion. A worker blocked in `ofThreadChannel::receive()` must be released by closing the channel.

Recommended destructor/`exit()` order:

1. Stop producers and external callbacks.
2. Close input and output channels so blocked calls wake.
3. Call `waitForThread(true)`.
4. Release objects that the worker referenced.
5. Remove any remaining event listeners.

The threaded image loader and channel example both close channels before joining. Sources: `openFrameworks/libs/openFrameworks/utils/ofThread.h`, `openFrameworks/addons/ofxThreadedImageLoader/src/ofxThreadedImageLoader.cpp`, `openFrameworks/examples/threads/threadChannelExample/src/ImgAnalysisThread.cpp`.

Avoid a polling loop that consumes a full core. Prefer blocking `receive()`; if polling is required, `ofThread::sleep()` or another wait primitive must yield CPU time. Catch anticipated exceptions inside `threadedFunction()` and report them with `ofLog*`; the `ofThread` contract notes that an escaping exception stops the thread. Source: `openFrameworks/libs/openFrameworks/utils/ofThread.h`.

## Event listener lifetime

An oF event subscription is an ownership relationship.

For oF versions that provide token listeners, prefer storing the token:

```cpp
class Controller {
public:
    void setup() {
        listeners.push(ofEvents().update.newListener(
            [this](ofEventArgs&) { update(); }));
    }

private:
    void update();
    ofEventListeners listeners;
};
```

`ofEvent<T>::newListener()` returns a token; `ofEventListener` owns one token, and `ofEventListeners` owns a collection. Destroying/resetting the token removes its callback. `unsubscribe()` and `unsubscribeAll()` allow explicit earlier removal. Source: `openFrameworks/libs/openFrameworks/events/ofEvent.h`.

Consequences:

- Store the token as a member whose lifetime matches the object used by the callback. A temporary token unsubscribes when it is destroyed.
- Ensure objects captured by a listener remain alive until unsubscription. Prefer capturing stable owners rather than stack references.
- In multi-window code, decide which app/window/state object owns each listener; context sharing does not solve listener lifetime.

For legacy registration, pair calls exactly:

```cpp
ofAddListener(ofEvents().update, this, &Controller::update, OF_EVENT_ORDER_AFTER_APP);
// before Controller is destroyed:
ofRemoveListener(ofEvents().update, this, &Controller::update, OF_EVENT_ORDER_AFTER_APP);
```

Removal uses the event, listener/function, method, and priority identity. Keep the same priority in both calls. Sources: `openFrameworks/libs/openFrameworks/events/ofEventUtils.h`, `openFrameworks/examples/events/advancedEventsExample/src/eventsObject.h`.

Event priorities are `OF_EVENT_ORDER_BEFORE_APP`, `OF_EVENT_ORDER_APP`, and `OF_EVENT_ORDER_AFTER_APP`. Do not change priority merely to hide an ownership or ordering bug. Source: `openFrameworks/libs/openFrameworks/events/ofEvent.h`.

## Frame timing and vertical sync

Distinguish measured timing from requested limits:

- `ofGetFrameRate()` returns the measured frame-rate counter.
- `ofGetTargetFrameRate()` returns the requested target.
- `ofGetTargetFrameRateEnabled()` reports whether a positive target is active.
- `ofGetLastFrameTime()` returns the last-frame duration according to the selected time mode.
- `ofSetFrameRate(rate)` enables target-rate waiting for a positive value and disables it for a non-positive value in the inspected implementation.

Sources: `openFrameworks/libs/openFrameworks/app/ofAppRunner.h`, `openFrameworks/libs/openFrameworks/events/ofEvents.cpp`, `openFrameworks/libs/openFrameworks/events/ofEvents.h`.

Use `ofGetLastFrameTime()` for frame-rate-independent state integration:

```cpp
position += velocityPixelsPerSecond * static_cast<float>(ofGetLastFrameTime());
```

Clamp or reset accumulated deltas when a paused debugger, sleep/wake, or blocking operation would make one unusually large step; the exact policy belongs to the app.

`ofSetVerticalSync(bool)` delegates to the current window. The GLFW implementation calls `glfwSwapInterval(1)` or `glfwSwapInterval(0)`. Treat VSync and `ofSetFrameRate()` as separate controls and measure their interaction on the target platform/window backend rather than promising an exact achieved FPS. Sources: `openFrameworks/libs/openFrameworks/app/ofAppRunner.cpp`, `openFrameworks/libs/openFrameworks/app/ofAppGLFWWindow.cpp`.

In multi-window code, timing and VSync are window-associated in the current API path. Call them with deliberate current-window ownership and follow the local windowing example; `multiWindowOneAppExample` explicitly changes VSync for its auxiliary window. Source: `openFrameworks/examples/windowing/multiWindowOneAppExample/src/main.cpp`.

## Streaming video lifecycle

For `ofVideoPlayer`:

1. Configure texture/pixel format options as required.
2. `load()`, then `play()` when playback should begin.
3. Call `update()` once per animation frame, normally in `ofApp::update()`.
4. Use `isFrameNew()` to gate expensive downstream work that only matters for new frames.
5. Call `close()` when replacing or releasing the stream.

The header explicitly documents the once-per-frame `update()` expectation. Its implementation asks the backend to update and uploads/reallocates textures only for new frames. Sources: `openFrameworks/libs/openFrameworks/video/ofVideoPlayer.h`, `openFrameworks/libs/openFrameworks/video/ofVideoPlayer.cpp`.

`ofVideoGrabber` follows the same update/new-frame/close rhythm around its capture backend. Its implementation updates the backend, uploads a texture for new frames when needed, and clears textures on close. Sources: `openFrameworks/libs/openFrameworks/video/ofVideoGrabber.h`, `openFrameworks/libs/openFrameworks/video/ofVideoGrabber.cpp`.

Do not assume that `draw()` advances capture or playback. Do not rerun expensive analysis/network sends on an unchanged frame. If a backend invokes native callbacks on another thread, keep that callback producer-only and hand CPU data/state to the main update path before touching oF OpenGL resources.

## Render-state isolation

Reusable draw functions should restore the state they change:

- `ofPushStyle()` / `ofPopStyle()` preserve drawing style.
- `ofPushMatrix()` / `ofPopMatrix()` preserve the current transform.
- `ofPushView()` / `ofPopView()` preserve viewport and matrix settings.
- `ofScopedStyle` and `ofScopedMatrix` provide scope-based style/matrix restoration.

Source: `openFrameworks/libs/openFrameworks/graphics/ofGraphics.h`.

Example:

```cpp
void Preview::draw(const ofRectangle& area) {
    ofScopedStyle style;
    ofScopedMatrix matrix;
    ofSetColor(255);
    ofTranslate(area.getTopLeft());
    texture.draw(0, 0, area.getWidth(), area.getHeight());
}
```

Use `ofPushView()`/`ofPopView()` when code changes viewport/view matrices; `viewportExample` demonstrates this pairing. Source: `openFrameworks/examples/gl/viewportExample/src/ofApp.cpp`.

Pair `camera.begin()`/`camera.end()`, `shader.begin()`/`shader.end()`, and `fbo.begin()`/`fbo.end()` on every path. Prefer small scopes or guard objects where the target code provides them so early returns cannot leak state.

`ofFbo::begin()` can set perspective, viewport, and Y-flip defaults according to `ofFboMode`. The header also warns that the convenience `begin()` path is unsafe in multi-window/multi-renderer scenarios and points to the renderer-specific begin API. Choose the mode deliberately when nested rendering already owns matrices/viewports. Source: `openFrameworks/libs/openFrameworks/gl/ofFbo.h`.

State isolation does not mean blindly pushing every API state. Blend, depth, culling, shader bindings, and raw OpenGL state should have an explicit owner and restoration policy; inspect the renderer and neighboring passes before adding direct GL calls.

## Agent checklist

Before accepting an oF runtime change:

- [ ] Relative assets resolve through the data-path API; no developer-machine absolute paths were introduced.
- [ ] CPU data and OpenGL resources have an explicit thread boundary.
- [ ] A live-frame queue has a documented drop/backpressure policy.
- [ ] Blocking worker waits can be released during shutdown, and threads are joined before referenced state is destroyed.
- [ ] Every event listener has a visible owner and unsubscription path.
- [ ] Texture/image/FBO allocation handles initial size and supported size/format changes.
- [ ] `update()` advances video/capture state; `isFrameNew()` gates per-frame downstream work.
- [ ] Frame-rate calculations use measured delta where appropriate; VSync and target FPS are not conflated.
- [ ] Modular draw code restores style, transform, viewport, render-target, shader, and camera state it owns.
- [ ] Claims and API names were checked against the target oF version's source/examples.
