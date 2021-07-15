const path = require("path");
const webpack = require("webpack");

const PUBLIC_PATH = "/static/frontend/dist/";

module.exports = {
  entry: {
    session: "./frontend/src/renders/renderSession.jsx",
  },
  output: {
    filename: "[name].bundle.js",
    chunkFilename: "[name].bundle.js",
    path: path.resolve(__dirname, "./frontend/static/frontend/dist/"),
    publicPath: PUBLIC_PATH,
  },
  module: {
    rules: [
      {
        test: [/\.m?js$/, /\.m?jsx$/],
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"],
          },
        },
      },
    ],
  },
  resolve: {
    extensions: [".js", ".jsx"],
  },
  plugins: [new webpack.EnvironmentPlugin(["API_URL"])],
};
