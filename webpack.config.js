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
	plugins: [
		// Ignore all locale files of moment.js
		// You can stillo import them by moment.locale('language');
		new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
	],
};
