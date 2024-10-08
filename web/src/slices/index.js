import { combineReducers } from "redux";

import ateam from "./ateam";
import auth from "./auth";
import pteam from "./pteam";
import system from "./system";
import tags from "./tags";
import topics from "./topics";
import user from "./user";

export const sliceReducers = { ateam, auth, pteam, system, tags, topics, user };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
