import { mkdtempSync, readFileSync, realpathSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { extname, isAbsolute, join, relative, resolve, sep } from "node:path";

const types = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".woff": "font/woff", ".mp4": "video/mp4" };

export function storyHandler(root, stage) {
  const directory = realpathSync(root);
  return (request, response) => {
    let path;
    try {
      path = decodeURIComponent(new URL(request.url, "http://local").pathname);
    } catch {
      response.writeHead(400);
      return response.end();
    }
    if (path === "/__stage.html") {
      response.writeHead(200, { "content-type": "text/html" });
      return response.end(stage);
    }
    try {
      const target = realpathSync(resolve(directory, "." + path.replace(/^\/__story\//, "/")));
      const contained = relative(directory, target);
      if (contained === ".." || contained.startsWith(".." + sep) || isAbsolute(contained)
          || !statSync(target).isFile()) {
        response.writeHead(404);
        return response.end();
      }
      const content = readFileSync(target);
      response.writeHead(200, { "content-type": types[extname(target).toLowerCase()] ?? "application/octet-stream" });
      return response.end(content);
    } catch {
      response.writeHead(404);
      return response.end();
    }
  };
}

export function frameDirectory() {
  // Only this newly allocated directory is owned by this render.
  const path = mkdtempSync(join(tmpdir(), "unslop-story-"));
  return { path, cleanup: () => rmSync(path, { recursive: true, force: true }) };
}
