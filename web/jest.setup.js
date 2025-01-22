import "@testing-library/jest-dom";
import { TextDecoder, TextEncoder, ReadableStream, Request, Response } from "node:util";

global.TextDecoder = TextDecoder;
global.TextEncoder = TextEncoder;
global.ReadableStream = ReadableStream;
global.Request = Request;
global.Response = Response;
