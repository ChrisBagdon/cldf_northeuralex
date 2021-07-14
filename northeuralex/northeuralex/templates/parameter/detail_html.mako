<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>


% if ctx.concepticon_name:
<h2>${_('Parameter')} ${ctx.concepticon_name}</h2>
% else:
<h2>${_('Parameter')} ${ctx.base_name.upper()}</h2>
% endif

% if ctx.description:
<p>${ctx.description}</p>
% endif

<div style="clear: both"/>
% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
