{ProfileView} = require 'views/profile_view'

class exports.ProfileRouter extends Backbone.Router
  routes:
    '!/profiles/': "index"
    '!/profiles/:id': "show"
    '!/profiles/:id/edit': "edit"

  initialize: ->
    unless @view?
      @view = new ProfileView

  index: -> @bindInject @view, {action: 'profile:index'}
  show: (id) -> @bindInject @view, {id: id, action: 'profile:show'}
  edit: (id) -> @bindInject @view, {id: id, action: 'profile:edit'}

  bindInject: (view, options) ->
    view.push options

    mediator.on options.action, (model) =>
      app.inject view.render {action: options.action, model: model}
      mediator.off options.action

    mediator.on 'all', (action, model) ->
      console.log 'action:', action, model
