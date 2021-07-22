const path = require("path");
const webpack = require("webpack");

module.exports = {
	mode: process.env.NODE_ENV,
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
		new webpack.EnvironmentPlugin([
			"NODE_ENV",
			"API_DOMAIN",
			"WEBSOCKET_DOMAIN",
		]),
	],
};
