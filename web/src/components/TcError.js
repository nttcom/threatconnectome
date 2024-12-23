export class TcError extends Error {
  constructor(message, customProps) {
    console.log(message, customProps);
    super(message);
    this.api = customProps.api;
  }
}
