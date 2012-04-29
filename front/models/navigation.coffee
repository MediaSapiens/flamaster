define [
  'chaplin/mediator', 'chaplin/model'
], (mediator, Model) ->
  'use strict'

  class Navigation extends Model
    defaults:
      routes: [
        {id: 'index', path: '', title: 'Index'}
        {id: 'signin', path: 'signin', title: 'Sign In'}
        {id: 'signup', path: 'signup', title: 'Sign Up'}
        {id: 'signout', path: 'signout', title: 'Sign Out'}
      ]
