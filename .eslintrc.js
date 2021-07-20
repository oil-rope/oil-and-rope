module.exports = {
	env: {
		browser: true,
		es2021: true,
		node: true,
	},
	parser: "babel-eslint",
	parserOptions: {
		ecmaFeatures: {
			jsx: true,
		},
	},
	plugins: ["react"],
	extends: [
		"eslint:recommended",
		"plugin:react/recommended",
		"plugin:prettier/recommended",
		"plugin:jest/recommended",
	],
	parserOptions: {
		ecmaFeatures: {
			jsx: true,
		},
		ecmaVersion: 12,
		sourceType: "module",
	},
	rules: {},
	settings: {
		react: {
			createClass: "createReactClass",
			pragma: "React",
			fragment: "Fragment",
			version: "detect",
			flowVersion: "0.53",
		},
		propWrapperFunctions: [
			"forbidExtraProps",
			{ property: "freeze", object: "Object" },
			{ property: "myFavoriteWrapper" },
		],
		componentWrapperFunctions: [
			"observer",
			{ property: "styled" },
			{ property: "observer", object: "Mobx" },
			{ property: "observer", object: "<pragma>" },
		],
		linkComponents: ["Hyperlink", { name: "Link", linkAttribute: "to" }],
	},
	globals: {
		gettext: "readonly",
	},
};
