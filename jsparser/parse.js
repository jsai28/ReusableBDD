const acorn = require("acorn");
const estraverse = require("estraverse");
const fs = require("fs");
const path = require("path");

function findJsFilesInStepDefinitions(baseDir) {
  const stepDefinitions = [];

  function walkSync(currentDirPath) {
    fs.readdirSync(currentDirPath).forEach((name) => {
      const filePath = path.join(currentDirPath, name);
      const stat = fs.statSync(filePath);
      if (stat.isDirectory()) {
        if (name === "step_definitions") {
          fs.readdirSync(filePath).forEach((file) => {
            if (file.endsWith(".js")) {
              console.log(file);
              stepDefinitions.push(path.join(filePath, file));
            }
          });
        } else {
          walkSync(filePath);
        }
      }
    });
  }

  walkSync(baseDir);
  return stepDefinitions;
}

function parser(code, filePath, result) {
  const ast = acorn.parse(code, { ecmaVersion: 2020 });

  estraverse.traverse(ast, {
    enter: (node, parent) => {
      if (
        node.type === "CallExpression" &&
        node.callee.type === "MemberExpression" &&
        node.callee.object.type === "ThisExpression" &&
        ["Given", "Then", "When", "And"].includes(node.callee.property.name)
      ) {
        const functionName = node.callee.property.name;
        const params = node.arguments.slice(0, -1).map((arg) => {
          let paramStr = code.slice(arg.start, arg.end);
          if (paramStr.startsWith("/") && paramStr.endsWith("/")) {
            paramStr = paramStr.slice(1, -1);
          }
          return paramStr;
        });
        const body = code.slice(
          node.arguments[node.arguments.length - 1].start,
          node.arguments[node.arguments.length - 1].end
        );
        result[params.join(", ")] = {
          Code: body,
          File: path.basename(filePath), // Only the file name
        };
      }
    },
  });
}

const feature_directory = path.resolve(
  __dirname,
  "../repos/aws-sdk-js/features"
);
const stepDefinitions = findJsFilesInStepDefinitions(feature_directory);
stepDefinitions.push("../repos/aws-sdk-js/features/extra/hooks.js");

const result = {};

stepDefinitions.forEach((filePath) => {
  const code = fs.readFileSync(filePath, "utf-8");
  parser(code, filePath, result);
});

// Write result to a JSON file
const outputFilePath = path.join(
  __dirname,
  "../data/aws-sdk-js/parsed_stepdefinitions.json"
);
fs.writeFileSync(outputFilePath, JSON.stringify(result, null, 2), "utf-8");

console.log(`Parsed functions have been written to ${outputFilePath}`);
