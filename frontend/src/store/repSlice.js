import { createSlice } from "@reduxjs/toolkit";

const repSlice = createSlice({
  name: "rep",
  initialState: {
    name: "",
  },
  reducers: {
    setRepName(state, action) {
      state.name = action.payload;
    },
  },
});

export const { setRepName } = repSlice.actions;
export default repSlice.reducer;
