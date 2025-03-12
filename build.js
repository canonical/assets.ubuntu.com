var esbuild = require("esbuild");

let entries = {
  main: "./static/js/src/main.js",
  navigation: "./static/js/src/navigation.js",
};

for (const [key, value] of Object.entries(entries)) {
  const options = {
    entryPoints: [value],
    bundle: true,
    outfile: `./static/js/dist/${key}.js`,
    target: ["chrome90", "firefox88", "safari14", "edge90"],
  };

  esbuild.build(options).catch(() => process.exit(1));
}
