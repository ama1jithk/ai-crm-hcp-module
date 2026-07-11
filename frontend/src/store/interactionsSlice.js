import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { InteractionAPI } from "../api/client";

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (payload) => {
    const res = await InteractionAPI.create(payload);
    return res.data;
  }
);

export const updateInteraction = createAsyncThunk(
  "interactions/update",
  async ({ id, payload }) => {
    const res = await InteractionAPI.update(id, payload);
    return res.data;
  }
);

const interactionsSlice = createSlice({
  name: "interactions",
  initialState: {
    items: [],
    formStatus: "idle",
    lastCreated: null,
  },
  reducers: {
    upsertInteractionLocal(state, action) {
      const idx = state.items.findIndex((i) => i.id === action.payload.id);
      if (idx >= 0) state.items[idx] = action.payload;
      else state.items.unshift(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createInteraction.pending, (state) => {
        state.formStatus = "saving";
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.formStatus = "succeeded";
        state.items.unshift(action.payload);
        state.lastCreated = action.payload;
      })
      .addCase(createInteraction.rejected, (state) => {
        state.formStatus = "failed";
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.items.findIndex((i) => i.id === action.payload.id);
        if (idx >= 0) state.items[idx] = action.payload;
      });
  },
});

export const { upsertInteractionLocal } = interactionsSlice.actions;
export default interactionsSlice.reducer;
