export class APIError extends Error {
  constructor(message, customProps) {
    super(message);
    this.api = customProps.api;
  }
}
