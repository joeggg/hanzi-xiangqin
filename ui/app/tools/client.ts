import axios from "axios";
import axiosRetry from "axios-retry";

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL,
});

axiosRetry(client, {
  retries: 5,
  retryDelay: axiosRetry.exponentialDelay,
});

export default client;
