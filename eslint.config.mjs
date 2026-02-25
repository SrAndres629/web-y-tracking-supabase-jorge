import js from "@eslint/js";
import globals from "globals";

export default [
    {
        ignores: ["**/node_modules/**", "**/venv/**", "**/static/dist/**", "**/.vscode/**", "**/__pycache__/**"]
    },
    js.configs.recommended,
    {
        files: ["**/*.js"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            globals: {
                ...globals.browser,
                ...globals.node,
                gsap: "readonly",
                Lenis: "readonly",
                ScrollTrigger: "readonly",
                Hammer: "readonly",
                Logger: "readonly",
            },
        },
        rules: {
            "no-unused-vars": "warn",
            "no-console": "off",
            "no-undef": "warn",
        },
    },
];
