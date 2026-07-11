import { createSlice, createAsyncThunk, nanoid } from "@reduxjs/toolkit";
import { ChatAPI } from "../api/client";

export const sendChatMessage = createAsyncThunk(
  "chat/send",
  async ({ message, hcpId, repName }, { getState }) => {
    const { chat } = getState();
    const res = await ChatAPI.send({
      session_id: chat.sessionId,
      message,
      hcp_id: hcpId,
      rep_name: repName,
    });
    return res.data;
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    sessionId: nanoid(),
    messages: [], 
    status: "idle",
  },
  reducers: {
    resetSession(state) {
      state.sessionId = nanoid();
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state, action) => {
        state.status = "loading";
        state.messages.push({ role: "user", content: action.meta.arg.message });
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.messages.push({
          role: "assistant",
          content: action.payload.reply,
          toolCalls: action.payload.tool_calls,
          interaction: action.payload.interaction,
        });
      })
      .addCase(sendChatMessage.rejected, (state) => {
        state.status = "failed";
        state.messages.push({
          role: "assistant",
          content: "Something went wrong reaching the agent. Please try again.",
        });
      });
  },
});

export const { resetSession } = chatSlice.actions;
export default chatSlice.reducer;
