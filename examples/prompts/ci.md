# openFrameworks CI prompts

- Use `$of-ci` to add `2bbb/of-actions` CI for this addon. Build Debug and Release, run its ofxUnitTests app, pin a verified workflow ref, and explain any tagged-workflow limitations that affect this repository.
- Use `$of-ci` to add conservative build-only CI for this standalone oF app on macOS, Linux, and Windows. Verify the repository layout and `Makefile` assumptions before writing YAML.
- Use `$of-ci` to audit this workflow's runner matrix, `test_mode`, no-window exit behavior, oF release selection, cache invalidation, and third-party workflow pinning against primary sources.
