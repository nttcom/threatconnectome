import { combineReducers } from "redux";

import auth from "./auth";

export const sliceReducers = { auth };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
