import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";
import { TextDecoder, TextEncoder, ReadableStream, Request, Response } from "node:util";

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
global.ReadableStream = ReadableStream;
global.Request = Request;
global.Response = Response;
