{ProfileView} = require 'views/profile_view'

class exports.ProfileRouter extends Backbone.Router
  routes:
    '!/profiles/': "index"
    '!/profiles/:id': "show"
    '!/profiles/:id/edit': "edit"

  initialize: (options) ->
    @mainRouter = options.mainRouter

  index: ->
    @ensureView()
    app.router.inject @profileView.render('index')
    console.log 'index'

  show: (id) ->
    @ensureView()
    app.router.inject @profileView.render('show')
    console.log 'show'

  edit: ->
    @ensureView()
    app.router.inject @profileView.render('edit')
    console.log 'edit'

  ensureView: ->
    console.log @profileView?
    if not @profileView?
      @profileView = app.router.renderDefault(ProfileView, {id: id})
    @profileView
