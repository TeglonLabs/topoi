#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const DRAND_API = "https://api.drand.sh";
const LEAGUE_OF_ENTROPY = "/drand/public/latest";

interface DrandResponse {
  round: number;
  randomness: string;
  signature: string;
  previous_signature: string;
}

export class BmorphismServer {
  private server: Server;
  private axiosInstance;

  constructor() {
    this.server = new Server(
      {
        name: "bmorphism-mcp",
        version: "0.1.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.axiosInstance = axios.create({
      baseURL: DRAND_API,
      timeout: 5000,
    });

    this.setupTools();
    this.setupErrorHandling();
  }

  private setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };

    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupTools() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "get_latest_randomness",
          description: "Get the latest randomness from drand League of Entropy",
          inputSchema: {
            type: "object",
            properties: {},
            required: [],
          },
        },
        {
          name: "get_round_info",
          description: "Get information about the current drand round",
          inputSchema: {
            type: "object",
            properties: {},
            required: [],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        switch (request.params.name) {
          case "get_latest_randomness": {
            const response = await this.axiosInstance.get<DrandResponse>(LEAGUE_OF_ENTROPY);
            return {
              content: [
                {
                  type: "text",
                  text: `Latest randomness: ${response.data.randomness}`,
                },
              ],
            };
          }

          case "get_round_info": {
            const response = await this.axiosInstance.get<DrandResponse>(LEAGUE_OF_ENTROPY);
            return {
              content: [
                {
                  type: "text",
                  text: JSON.stringify(
                    {
                      round: response.data.round,
                      signature: response.data.signature,
                      previous_signature: response.data.previous_signature,
                    },
                    null,
                    2
                  ),
                },
              ],
            };
          }

          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${request.params.name}`
            );
        }
      } catch (error) {
        if (axios.isAxiosError(error)) {
          return {
            content: [
              {
                type: "text",
                text: `Drand API error: ${error.response?.data?.message ?? error.message}`,
              },
            ],
            isError: true,
          };
        }
        throw error;
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Bmorphism MCP Server (TypeScript) running on stdio");
  }
}

const server = new BmorphismServer();
server.run().catch(console.error);
