import * as params from '@params';

const input = document.getElementById('searchInput');
const suggestionList = document.getElementById('searchSuggestions');
const resultList = document.getElementById('searchResults');
const status = document.getElementById('searchStatus');
const categoryFilter = document.getElementById('categoryFilter');
const seriesFilter = document.getElementById('seriesFilter');
const yearFilter = document.getElementById('yearFilter');

let documents = [];
let fuse = null;
let debounceTimer = null;

function addOptions(select, values) {
    [...new Set(values.filter(Boolean))]
        .sort((a, b) => String(a).localeCompare(String(b), 'ko'))
        .forEach((value) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        });
}

function includesValue(values, expected) {
    return !expected || (Array.isArray(values) && values.includes(expected));
}

function hideSuggestions() {
    suggestionList.hidden = true;
    suggestionList.replaceChildren();
    input.setAttribute('aria-expanded', 'false');
}

function chooseSuggestion(value) {
    input.value = value;
    hideSuggestions();
    search();
    input.focus();
}

function renderSuggestions() {
    if (!documents.length) return;
    const query = input.value.trim().toLocaleLowerCase('ko');
    if (!query) {
        hideSuggestions();
        return;
    }

    const candidates = [];
    const seen = new Set();
    function collect(value, kind) {
        if (!value) return;
        const normalized = String(value).toLocaleLowerCase('ko');
        if (!normalized.includes(query) || seen.has(normalized)) return;
        seen.add(normalized);
        candidates.push({
            value: String(value),
            kind,
            startsWith: normalized.startsWith(query)
        });
    }

    documents.forEach((item) => {
        collect(item.title, '글 제목');
        (item.tags || []).forEach((tag) => collect(tag, '태그'));
        (item.series || []).forEach((series) => collect(series, '시리즈'));
    });

    const suggestions = candidates
        .sort((a, b) => Number(b.startsWith) - Number(a.startsWith) || a.value.length - b.value.length || a.value.localeCompare(b.value, 'ko'))
        .slice(0, 8);

    suggestionList.replaceChildren();
    suggestions.forEach((suggestion) => {
        const row = document.createElement('li');
        row.setAttribute('role', 'option');
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'search-suggestion';
        const value = document.createElement('span');
        value.textContent = suggestion.value;
        const kind = document.createElement('small');
        kind.textContent = suggestion.kind;
        button.append(value, kind);
        button.addEventListener('click', () => chooseSuggestion(suggestion.value));
        row.appendChild(button);
        suggestionList.appendChild(row);
    });

    suggestionList.hidden = suggestions.length === 0;
    input.setAttribute('aria-expanded', suggestions.length ? 'true' : 'false');
}

function renderResults(items) {
    resultList.replaceChildren();

    items.forEach((item) => {
        const row = document.createElement('li');
        row.className = 'post-entry';

        const header = document.createElement('header');
        header.className = 'entry-header';

        const title = document.createElement('span');
        title.className = 'search-result-title';
        title.textContent = `${item.title} »`;
        header.appendChild(title);

        if (item.description) {
            const description = document.createElement('span');
            description.className = 'search-result-description';
            description.textContent = item.description;
            header.appendChild(description);
        }

        const meta = document.createElement('span');
        meta.className = 'search-result-meta';
        meta.textContent = [item.date, ...(item.categories || []), ...(item.series || [])]
            .filter(Boolean)
            .join(' · ');
        header.appendChild(meta);

        const link = document.createElement('a');
        link.href = item.permalink;
        link.setAttribute('aria-label', item.title);

        row.append(header, link);
        resultList.appendChild(row);
    });
}

function search() {
    if (!fuse) return;

    const query = input.value.trim();
    const category = categoryFilter.value;
    const series = seriesFilter.value;
    const year = yearFilter.value;
    const hasFilters = category || series || year;

    if (!query && !hasFilters) {
        resultList.replaceChildren();
        status.textContent = '검색어를 입력하거나 필터를 선택하세요.';
        return;
    }

    const candidates = query
        ? fuse.search(query, { limit: documents.length }).map((result) => result.item)
        : documents;

    const filtered = candidates.filter((item) =>
        includesValue(item.categories, category) &&
        includesValue(item.series, series) &&
        (!year || item.year === year)
    );
    const limit = params.fuseOpts?.limit ?? 50;
    renderResults(filtered.slice(0, limit));
    status.textContent = filtered.length
        ? `${filtered.length}개 결과${filtered.length > limit ? ` 중 ${limit}개 표시` : ''}`
        : '일치하는 글이 없습니다.';
}

function scheduleSearch() {
    renderSuggestions();
    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(search, 100);
}

async function loadIndex() {
    try {
        const response = await fetch('../index.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        documents = await response.json();
        const options = {
            isCaseSensitive: params.fuseOpts?.iscasesensitive ?? false,
            shouldSort: params.fuseOpts?.shouldsort ?? true,
            ignoreLocation: true,
            threshold: params.fuseOpts?.threshold ?? 0.35,
            minMatchCharLength: params.fuseOpts?.minmatchcharlength ?? 1,
            keys: params.fuseOpts?.keys ?? ['title', 'description', 'headings', 'categories', 'tags', 'series']
        };
        fuse = new Fuse(documents, options);

        addOptions(categoryFilter, documents.flatMap((item) => item.categories || []));
        addOptions(seriesFilter, documents.flatMap((item) => item.series || []));
        addOptions(yearFilter, documents.map((item) => item.year).sort().reverse());
        status.textContent = '검색어를 입력하거나 필터를 선택하세요.';
    } catch (error) {
        status.textContent = '검색 인덱스를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.';
        console.error('Search index load failed', error);
    }
}

input.addEventListener('input', scheduleSearch);
input.addEventListener('search', search);
[categoryFilter, seriesFilter, yearFilter].forEach((select) => select.addEventListener('change', search));

input.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') {
        const firstSuggestion = suggestionList.querySelector('button');
        const firstLink = resultList.querySelector('a');
        if (firstSuggestion || firstLink) {
            event.preventDefault();
            (firstSuggestion || firstLink).focus();
        }
    } else if (event.key === 'Escape') {
        if (!suggestionList.hidden) {
            hideSuggestions();
        } else {
            input.value = '';
            categoryFilter.value = '';
            seriesFilter.value = '';
            yearFilter.value = '';
            search();
        }
    }
});

suggestionList.addEventListener('keydown', (event) => {
    if (!['ArrowDown', 'ArrowUp', 'Escape'].includes(event.key)) return;
    const buttons = [...suggestionList.querySelectorAll('button')];
    const current = buttons.indexOf(document.activeElement);
    if (event.key === 'Escape') {
        event.preventDefault();
        hideSuggestions();
        input.focus();
        return;
    }
    if (current < 0) return;
    event.preventDefault();
    if (event.key === 'ArrowDown' && current < buttons.length - 1) buttons[current + 1].focus();
    if (event.key === 'ArrowDown' && current === buttons.length - 1) {
        const firstResult = resultList.querySelector('a');
        if (firstResult) firstResult.focus();
    }
    if (event.key === 'ArrowUp' && current > 0) buttons[current - 1].focus();
    if (event.key === 'ArrowUp' && current === 0) input.focus();
});

resultList.addEventListener('keydown', (event) => {
    if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;
    const links = [...resultList.querySelectorAll('a')];
    const current = links.indexOf(document.activeElement);
    if (current < 0) return;
    event.preventDefault();
    if (event.key === 'ArrowDown' && current < links.length - 1) links[current + 1].focus();
    if (event.key === 'ArrowUp' && current > 0) links[current - 1].focus();
    if (event.key === 'ArrowUp' && current === 0) input.focus();
});

document.addEventListener('click', (event) => {
    if (!document.getElementById('searchbox').contains(event.target)) hideSuggestions();
});

loadIndex();
