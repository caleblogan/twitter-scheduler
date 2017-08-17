const path = require('path');

const config = {
  entry: './twitterscheduler/static/twitterscheduler/js/lib/index.js',
  output: {
    path: path.resolve(__dirname, './twitterscheduler/static/twitterscheduler/js/'),
    // publicPath: '/static/',
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['env']
          }
        }
      }
    ]
  }
};

module.exports = config;
