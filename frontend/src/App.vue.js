import { computed, ref } from 'vue';
import { requestReflection } from './api';
const maxLength = 3000;
const situation = ref('');
const reflection = ref(null);
const loading = ref(false);
const error = ref('');
const tips = [
    'Describe the facts before your interpretation of them.',
    'Include the decision you are trying to make.',
    'Mention who may be helped or harmed by the decision.',
    'Leave out names, addresses, and identifying details.',
];
const canSubmit = computed(() => situation.value.trim().length >= 20 && !loading.value);
async function submit() {
    if (!canSubmit.value)
        return;
    loading.value = true;
    error.value = '';
    reflection.value = null;
    try {
        reflection.value = await requestReflection(situation.value.trim());
    }
    catch (caught) {
        error.value = caught instanceof Error ? caught.message : 'Something went wrong.';
    }
    finally {
        loading.value = false;
    }
}
function reset() {
    reflection.value = null;
    error.value = '';
    situation.value = '';
}
const __VLS_ctx = {
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "page-shell" },
});
/** @type {__VLS_StyleScopedClasses['page-shell']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.header, __VLS_intrinsics.header)({
    ...{ class: "site-header" },
});
/** @type {__VLS_StyleScopedClasses['site-header']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.a, __VLS_intrinsics.a)({
    ...{ class: "wordmark" },
    href: "#",
    'aria-label': "WWJD home",
});
/** @type {__VLS_StyleScopedClasses['wordmark']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
    ...{ class: "wordmark-mark" },
});
/** @type {__VLS_StyleScopedClasses['wordmark-mark']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
    ...{ class: "header-note" },
});
/** @type {__VLS_StyleScopedClasses['header-note']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.main, __VLS_intrinsics.main)({});
if (!__VLS_ctx.reflection) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
        ...{ class: "hero" },
        'aria-labelledby': "page-title",
    });
    /** @type {__VLS_StyleScopedClasses['hero']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "eyebrow" },
    });
    /** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.h1, __VLS_intrinsics.h1)({
        id: "page-title",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.br)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.em, __VLS_intrinsics.em)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "intro" },
    });
    /** @type {__VLS_StyleScopedClasses['intro']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.form, __VLS_intrinsics.form)({
        ...{ onSubmit: (__VLS_ctx.submit) },
        ...{ class: "prompt-card" },
    });
    /** @type {__VLS_StyleScopedClasses['prompt-card']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.label, __VLS_intrinsics.label)({
        for: "situation",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.textarea, __VLS_intrinsics.textarea)({
        id: "situation",
        value: (__VLS_ctx.situation),
        maxlength: (__VLS_ctx.maxLength),
        rows: "7",
        placeholder: "I’m struggling with a decision at work...",
        'aria-describedby': "prompt-help",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "field-footer" },
    });
    /** @type {__VLS_StyleScopedClasses['field-footer']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        id: "prompt-help",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
    (__VLS_ctx.situation.length);
    (__VLS_ctx.maxLength);
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        type: "submit",
        disabled: (!__VLS_ctx.canSubmit),
    });
    if (__VLS_ctx.loading) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            ...{ class: "spinner" },
            'aria-hidden': "true",
        });
        /** @type {__VLS_StyleScopedClasses['spinner']} */ ;
    }
    (__VLS_ctx.loading ? 'Reflecting…' : 'Find a way forward');
    if (!__VLS_ctx.loading) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            'aria-hidden': "true",
        });
    }
    if (__VLS_ctx.error) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
            ...{ class: "error" },
            role: "alert",
        });
        /** @type {__VLS_StyleScopedClasses['error']} */ ;
        (__VLS_ctx.error);
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.aside, __VLS_intrinsics.aside)({
        ...{ class: "tips" },
        'aria-labelledby': "tips-title",
    });
    /** @type {__VLS_StyleScopedClasses['tips']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        id: "tips-title",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.ul, __VLS_intrinsics.ul)({});
    for (const [tip] of __VLS_vFor((__VLS_ctx.tips))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.li, __VLS_intrinsics.li)({
            key: (tip),
        });
        (tip);
        // @ts-ignore
        [reflection, submit, situation, situation, maxLength, maxLength, canSubmit, loading, loading, loading, error, error, tips,];
    }
}
else {
    __VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
        ...{ class: "result" },
        'aria-live': "polite",
    });
    /** @type {__VLS_StyleScopedClasses['result']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.reset) },
        ...{ class: "back-button" },
        type: "button",
    });
    /** @type {__VLS_StyleScopedClasses['back-button']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "result-heading" },
    });
    /** @type {__VLS_StyleScopedClasses['result-heading']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "eyebrow" },
    });
    /** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.h1, __VLS_intrinsics.h1)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.br)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.em, __VLS_intrinsics.em)({});
    if (__VLS_ctx.reflection.safety_message) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ class: "safety" },
            role: "alert",
        });
        /** @type {__VLS_StyleScopedClasses['safety']} */ ;
        __VLS_asFunctionalElement1(__VLS_intrinsics.strong, __VLS_intrinsics.strong)({});
        __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({});
        (__VLS_ctx.reflection.safety_message);
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.article, __VLS_intrinsics.article)({
        ...{ class: "reflection-card" },
    });
    /** @type {__VLS_StyleScopedClasses['reflection-card']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "summary" },
    });
    /** @type {__VLS_StyleScopedClasses['summary']} */ ;
    (__VLS_ctx.reflection.summary);
    __VLS_asFunctionalElement1(__VLS_intrinsics.h2, __VLS_intrinsics.h2)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.ol, __VLS_intrinsics.ol)({});
    for (const [action] of __VLS_vFor((__VLS_ctx.reflection.suggested_actions))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.li, __VLS_intrinsics.li)({
            key: (action),
        });
        (action);
        // @ts-ignore
        [reflection, reflection, reflection, reflection, reset,];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
        ...{ class: "sources" },
        'aria-labelledby': "sources-title",
    });
    /** @type {__VLS_StyleScopedClasses['sources']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "section-heading" },
    });
    /** @type {__VLS_StyleScopedClasses['section-heading']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({});
    __VLS_asFunctionalElement1(__VLS_intrinsics.h2, __VLS_intrinsics.h2)({
        id: "sources-title",
    });
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "source-grid" },
    });
    /** @type {__VLS_StyleScopedClasses['source-grid']} */ ;
    for (const [source] of __VLS_vFor((__VLS_ctx.reflection.sources))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.figure, __VLS_intrinsics.figure)({
            key: (source.reference),
            ...{ class: "source-card" },
        });
        /** @type {__VLS_StyleScopedClasses['source-card']} */ ;
        __VLS_asFunctionalElement1(__VLS_intrinsics.blockquote, __VLS_intrinsics.blockquote)({});
        (source.quotation);
        __VLS_asFunctionalElement1(__VLS_intrinsics.figcaption, __VLS_intrinsics.figcaption)({});
        __VLS_asFunctionalElement1(__VLS_intrinsics.strong, __VLS_intrinsics.strong)({});
        (source.reference);
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
        (source.translation);
        if (source.context_note) {
            __VLS_asFunctionalElement1(__VLS_intrinsics.small, __VLS_intrinsics.small)({});
            (source.context_note);
        }
        // @ts-ignore
        [reflection,];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "limitations" },
    });
    /** @type {__VLS_StyleScopedClasses['limitations']} */ ;
    (__VLS_ctx.reflection.limitations);
}
__VLS_asFunctionalElement1(__VLS_intrinsics.footer, __VLS_intrinsics.footer)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
// @ts-ignore
[reflection,];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
