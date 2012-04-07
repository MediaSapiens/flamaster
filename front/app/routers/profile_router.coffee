{ProfileView} = require 'views/profile_view'

class exports.ProfileRouter extends Backbone.Router
  routes:
    '!/profiles/': "index"
    '!/profiles/:id': "show"
    '!/profiles/:id/edit': "edit"

  initialize: ->
    unless @view?
      @view = new ProfileView({routes: @routes})

  index: ->
    @bindInject @view, 'index'
    @view.push({action: 'index'})

  show: (id) ->
    @bindInject @view, 'show'
    @view.push({id: id, action: 'show'})

  edit: (id) ->
    @bindInject @view, 'edit'
    app.inject(@view.push({id: id, action: 'edit'}))

  bindInject: (view, action) ->
    view.on action, (args...) =>
      app.inject view.render()
