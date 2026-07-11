import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { HcpAPI } from "../api/client";

export const fetchHcps = createAsyncThunk("hcps/fetchAll", async () => {
  const res = await HcpAPI.list();
  return res.data;
});

export const fetchHcpHistory = createAsyncThunk("hcps/fetchHistory", async (hcpId) => {
  const res = await HcpAPI.history(hcpId);
  return { hcpId, history: res.data };
});

const hcpSlice = createSlice({
  name: "hcps",
  initialState: {
    list: [],
    selectedHcpId: null,
    historyByHcp: {},
    status: "idle",
  },
  reducers: {
    selectHcp(state, action) {
      state.selectedHcpId = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.list = action.payload;
        if (!state.selectedHcpId && action.payload.length) {
          state.selectedHcpId = action.payload[0].id;
        }
      })
      .addCase(fetchHcpHistory.fulfilled, (state, action) => {
        state.historyByHcp[action.payload.hcpId] = action.payload.history;
      });
  },
});

export const { selectHcp } = hcpSlice.actions;
export default hcpSlice.reducer;
