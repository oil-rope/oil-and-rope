const path = require("path");

const PUBLIC_PATH = process.env.STATIC_URL || "/static/frontend/dist/";

module.exports = {
	entry: {
<<<<<<< HEAD
		Calendar: "./frontend/src/renderCalendar.js",
		UserCheckButton: "./frontend/src/renderUserCheckButton.js",
		Chat: "./frontend/src/renderChat.js",
		Messages: "./frontend/src/renderMessages.js"
=======
		Calendar: "./frontend/src/renderCalendar.jsx",
		UserCheckButton: "./frontend/src/renderUserCheckButton.jsx",
>>>>>>> 7eabb0ff42fd3f7195c3a5b466323a639b70d2a5
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
