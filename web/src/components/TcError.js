export class TcError extends Error {
  constructor(message, customProps) {
    super(message);
    this.api = customProps.api;
  }
}
