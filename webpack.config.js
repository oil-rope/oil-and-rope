const path = require("path");

module.exports = {
	entry: {
		Calendar: "./frontend/src/renderCalendar.js",
		UserCheckButton: "./frontend/src/renderUserCheckButton.js",
	},
	output: {
		filename: "[name].bundle.js",
		path: path.resolve(__dirname, "./frontend/static/frontend/dist/"),
		chunkFilename: "[name].bundle.js",
	},
	devServer: {
		contentBase: "dist",
	},
	module: {
		rules: [
			{
				test: [/\.js$/, /\.jsx$/],
				exclude: /node_modules/,
				use: [
					{
						loader: "babel-loader",
					},
				],
			},
			{
				test: /\.s[ac]ss$/i,
				use: [
					// Creates `style` nodes from JS strings
					"style-loader",
					// // Translates CSS into CommonJS
					"css-loader",
					// // Compiles Sass to CSS
					"sass-loader",
				],
			},
		],
	},
	resolve: {
		extensions: [".js", ".jsx", ".scss", ".sass"],
	},
};
