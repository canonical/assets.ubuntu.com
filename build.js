var esbuild = require("esbuild");

esbuild.build({
  entryPoints: ["./static/js/src/main.js"], 
  bundle: true,
  outfile: "./static/js/dist/main.js",
  target: ["chrome90", "firefox88", "safari14", "edge90"],
}).catch(() => process.exit(1));