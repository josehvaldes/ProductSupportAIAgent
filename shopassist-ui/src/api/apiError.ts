// Error handling
export class ApiError extends Error {
  status: number;
  response: any | undefined;

  constructor(
    message: string,
    status: number,
    response?: any
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}