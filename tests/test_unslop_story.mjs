import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { frameDirectory, storyHandler } from "../skills/unslop/scripts/story-io.mjs";

test("story assets stay inside the real story directory and malformed requests are handled", () => {
  const fixture = mkdtempSync(join(tmpdir(), "unslop-io-test-"));
  try {
    const root = join(fixture, "story");
    const sibling = join(fixture, "story-private");
    mkdirSync(root);
    mkdirSync(sibling);
    writeFileSync(join(root, "index.html"), "story content");
    writeFileSync(join(sibling, "secret.txt"), "private data");
    mkdirSync(join(root, "directory"));
    symlinkSync(sibling, join(root, "linked-private"), process.platform === "win32" ? "junction" : "dir");
    const handler = storyHandler(root, "stage content");
    const request = (url) => {
      const result = {};
      handler({ url }, {
        writeHead(status, headers) { result.status = status; result.headers = headers; },
        end(body) { result.body = body?.toString(); },
      });
      return result;
    };
    assert.equal(request("/__stage.html").body, "stage content");
    assert.equal(request("/__story/index.html").body, "story content");
    assert.equal(request("/index.html").status, 200);
    for (const path of ["/__story/..%2fstory-private%2fsecret.txt", "/__story/..%5cstory-private%5csecret.txt",
                        "/__story/linked-private/secret.txt", "/__story/missing.txt", "/__story/directory",
                        "/__story/%00"]) {
      assert.equal(request(path).status, 404, path);
      assert.equal(request(path).body, undefined, path);
    }
    assert.equal(request("/__story/%invalid").status, 400);
    assert.equal(request("http://[").status, 400);
    assert.equal(request("/__story/index.html").body, "story content");
  } finally {
    rmSync(fixture, { recursive: true, force: true });
  }
});

test("concurrent frame directories are distinct and cleanup preserves unrelated files", () => {
  const fixture = mkdtempSync(join(tmpdir(), "unslop-frame-test-"));
  const first = frameDirectory();
  const second = frameDirectory();
  try {
    const legacy = join(fixture, ".story-frames");
    mkdirSync(legacy);
    writeFileSync(join(legacy, "keep.txt"), "unrelated");
    writeFileSync(join(first.path, "frame.jpg"), "first render");
    writeFileSync(join(second.path, "frame.jpg"), "second render");
    assert.notEqual(first.path, second.path);
    first.cleanup();
    assert.equal(existsSync(first.path), false);
    assert.equal(readFileSync(join(second.path, "frame.jpg"), "utf8"), "second render");
    assert.equal(readFileSync(join(legacy, "keep.txt"), "utf8"), "unrelated");
  } finally {
    first.cleanup();
    second.cleanup();
    rmSync(fixture, { recursive: true, force: true });
  }
});
