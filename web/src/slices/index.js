import { combineReducers } from "redux";

import ateam from "./ateam";
import auth from "./auth";
import system from "./system";

export const sliceReducers = { ateam, auth, system };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
