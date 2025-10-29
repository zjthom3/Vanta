const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApiError = {
  message: string;
  status: number;
};

type RequestOptions = {
  userId?: string;
  signal?: AbortSignal;
  cache?: RequestCache;
};

function buildHeaders(
  userId: string | undefined,
  additional: Record<string, string> = {},
): HeadersInit {
  const headers: Record<string, string> = { ...additional };
  if (userId) {
    headers["X-User-Id"] = userId;
  }
  return headers;
}

async function handleResponse<TResult>(response: Response): Promise<TResult> {
  if (!response.ok) {
    const message = await response.text();
    throw {
      message: message || response.statusText,
      status: response.status,
    } satisfies ApiError;
  }
  if (response.status === 204) {
    return null as unknown as TResult;
  }
  return (await response.json()) as TResult;
}

export async function getJson<TResult>(path: string, options: RequestOptions = {}): Promise<TResult> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "GET",
    headers: buildHeaders(options.userId),
    signal: options.signal,
    cache: options.cache,
  });
  return handleResponse<TResult>(response);
}

export async function postJson<TBody extends object, TResult>(
  path: string,
  body: TBody,
  options: RequestOptions = {},
): Promise<TResult> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: buildHeaders(options.userId, { "Content-Type": "application/json" }),
    body: JSON.stringify(body),
    signal: options.signal,
  });
  return handleResponse<TResult>(response);
}

export async function postFormData<TResult>(
  path: string,
  formData: FormData,
  options: RequestOptions = {},
): Promise<TResult> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: buildHeaders(options.userId),
    body: formData,
    signal: options.signal,
  });
  return handleResponse<TResult>(response);
}

export async function putJson<TBody extends object, TResult>(
  path: string,
  body: TBody,
  options: RequestOptions = {},
): Promise<TResult> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "PUT",
    headers: buildHeaders(options.userId, { "Content-Type": "application/json" }),
    body: JSON.stringify(body),
    signal: options.signal,
  });
  return handleResponse<TResult>(response);
}

export async function deleteRequest(path: string, options: RequestOptions = {}): Promise<void> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "DELETE",
    headers: buildHeaders(options.userId),
    signal: options.signal,
  });
  await handleResponse<void>(response);
}
