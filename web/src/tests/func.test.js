import { pickParentTagName } from "../utils/func";

test.each([
  { child: "scanelf:alpine-3.18.4:", parent: "scanelf:alpine-3.18.4:" },
  { child: "python-dotenv:pypi:python-pkg", parent: "python-dotenv:pypi:" },
  { child: "a:b:c", parent: "a:b:" },
])("pickParentTagName test", ({ child, parent }) => {
  expect(pickParentTagName(child)).toBe(parent);
});
