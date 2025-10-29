module.exports = {
  root: true,
  extends: ["next", "next/core-web-vitals"],
  parserOptions: {
    project: ["./tsconfig.json"],
  },
  rules: {
    "@next/next/no-html-link-for-pages": "off",
    "react/jsx-props-no-spreading": "off",
  },
};
