import { combineReducers } from "redux";

import ateam from "./ateam";
import auth from "./auth";
import pteam from "./pteam";
import system from "./system";
import topics from "./topics";

export const sliceReducers = { ateam, auth, pteam, system, topics };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
