import { apiClient, shouldUseMock } from "./client";
import type {
  ConversationResponse,
  ConversationSummaryResponse,
  SendMessageRequest,
} from "@/types";

export async function sendMessage(data: SendMessageRequest): Promise<ConversationResponse> {
  if (shouldUseMock("assistant")) {
    return {
      id: data.conversation_id || "conv-mock-1",
      title: "Workspace Guidance",
      messages: [
        {
          id: "msg-1",
          role: "user",
          content: data.message,
          created_at: new Date().toISOString(),
        },
        {
          id: "msg-2",
          role: "assistant",
          content: `I've analyzed your workspace context. Based on your current profile and goals, your next strongest move is to strengthen your Systems Thinking capability with a concrete project implementation or assessment check.`,
          created_at: new Date().toISOString(),
        },
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
  return apiClient<ConversationResponse>("/assistant/messages", {
    method: "POST",
    body: data,
  });
}

export async function listConversations(): Promise<ConversationSummaryResponse[]> {
  if (shouldUseMock("assistant")) {
    return [
      {
        id: "conv-mock-1",
        title: "Workspace Guidance",
        message_count: 2,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<ConversationSummaryResponse[]>("/assistant/conversations", {
    method: "GET",
  });
}

export async function getConversation(conversationId: string): Promise<ConversationResponse> {
  if (shouldUseMock("assistant")) {
    return sendMessage({ message: "Hello", conversation_id: conversationId });
  }
  return apiClient<ConversationResponse>(`/assistant/conversations/${conversationId}`, {
    method: "GET",
  });
}

export async function deleteConversation(conversationId: string): Promise<{ message: string }> {
  if (shouldUseMock("assistant")) {
    return { message: "Conversation deleted (mock)." };
  }
  return apiClient<{ message: string }>(`/assistant/conversations/${conversationId}`, {
    method: "DELETE",
  });
}
