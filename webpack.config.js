const path = require("path");
const webpack = require("webpack");

module.exports = {
	entry: {
		session: "./frontend/src/renders/renderSession.jsx",
	},
	output: {
		filename: "[name].bundle.js",
		path: path.resolve(__dirname, "./frontend/static/frontend/dist/"),
		clean: true,
	},
	module: {
		rules: [
			{
				test: [/\.m?js$/, /\.m?jsx$/],
				exclude: /node_modules/,
				use: "babel-loader",
			},
		],
	},
	resolve: {
		extensions: [".js", ".jsx"],
	},
	externals: {
		gettext: "gettext",
	},
	plugins: [
		new webpack.EnvironmentPlugin({
			WEBSOCKET_URL: "127.0.0.1:8000",
			API_URL: "127.0.0.1:8000",
			NODE_ENV: "development",
		}),
	],
};
