const path = require("path");

const PUBLIC_PATH = process.env.STATIC_URL || "/static/frontend/dist/";

module.exports = {
	entry: {
		Calendar: "./frontend/src/renderCalendar.jsx",
		UserCheckButton: "./frontend/src/renderUserCheckButton.jsx",
		TreeView: "./frontend/src/renderTreeView.jsx"
	},
	output: {
		publicPath: PUBLIC_PATH,
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
	externals: {
		jquery: 'jQuery'
	}
};
