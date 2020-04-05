module.exports = {
  module: {
    rules: [
      {
        test: [/\.js$/, /\.jsx$/],
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
          }
        ]
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          // Creates `style` nodes from JS strings
          "style-loader",
          // // Translates CSS into CommonJS
          "css-loader",
          // // Compiles Sass to CSS
          "sass-loader"
        ]
      }
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx', '.scss', '.sass']
  }
};
