const plugins = [
  [
    'babel-plugin-import',
    {
      libraryName: '@mui/material',
      libraryDirectory: '',
      camel2DashComponentName: false,
    },
    'core',
  ],
  [
    'babel-plugin-import',
    {
      libraryName: '@mui/icons-material',
      libraryDirectory: '',
      camel2DashComponentName: false,
    },
    'icons',
  ],
  [
    "module:react-native-dotenv",
    {
      "path": "./.env.test",
    },
  ],
];

const presets = ["@babel/preset-react", "@babel/preset-env"];

module.exports = { plugins, presets };
