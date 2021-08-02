module.exports = {
	env: {
		browser: true,
		es2021: true,
		node: true,
		"jest/globals": true,
	},
	extends: ["plugin:react/recommended", "airbnb", "prettier"],
	parser: "@babel/eslint-parser",
	parserOptions: {
		ecmaFeatures: {
			jsx: true,
		},
		ecmaVersion: 12,
		sourceType: "module",
	},
	plugins: ["react", "react-hooks", "prettier", "jest"],
	rules: {
		"react/jsx-filename-extension": [1, { extensions: [".js", ".jsx"] }],
		"no-console": ["error", { allow: ["error"] }],
		"jest/no-disabled-tests": "warn",
		"jest/no-focused-tests": "error",
		"jest/no-identical-title": "error",
		"jest/prefer-to-have-length": "warn",
		"jest/valid-expect": "error",
	},
	globals: {
		gettext: "readonly",
	},
};
