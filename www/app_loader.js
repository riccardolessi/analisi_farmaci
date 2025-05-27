import define from "./index.js";
import {Runtime, Inspector} from "../prova/runtime.js";

const target = document.getElementById("observable-target")

const runtime = new Runtime();
runtime.module(define, name => {
    return new Inspector(target)}
);
