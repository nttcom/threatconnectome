export class APIError extends Error {
  public readonly api: string;
  constructor(message: string, customProps: { api: string }) {
    super(message);
    this.api = customProps.api;
  }
}
