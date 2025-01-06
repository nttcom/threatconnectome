import { pickParentTagName } from "../utils/func";

const tagNames = [
  { child: "scanelf:alpine-3.18.4:", parent: "scanelf:alpine-3.18.4:" },
  { child: "python-dotenv:pypi:python-pkg", parent: "python-dotenv:pypi:" },
  { child: "a:b:c", parent: "a:b:" },
];

test("pickParentTagName test", () => {
  tagNames.forEach((tagName) => expect(pickParentTagName(tagName.child)).toBe(tagName.parent));
});
