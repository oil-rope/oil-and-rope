module.exports = {
  module: {
    rules: [
      {
        test: [/\.s[ac]ss$/, /\.jsx$/, /\.js$/],
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
          },
          // Creates `style` nodes from JS strings
          // "style-loader",
          // // Translates CSS into CommonJS
          // "css-loader",
          // // Compiles Sass to CSS
          // "sass-loader",
        ],
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  }
};
