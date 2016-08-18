import { Component } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { AuthService } from './services/auth';

@Component({
  selector: 'app',
  template: `
<div class='row'>
  <div class='col-sm-2'>
    <header>
      <h1>#cephilis</h1>
      <em>Get yours at Mirantis!</em>
    </header>
  </div>
  <div class='col-sm-10'>
    <navigation *ngIf='auth.isLoggedIn()'>
      <ul>
        <li> <a [routerLink]="['/clusters']" routerLinkActive='active'>Clusters</a>
        <li> <a [routerLink]="['/configurations']" routerLinkActive='active'>Configurations</a>
        <li> <a [routerLink]="['/playbooks']" routerLinkActive='active'>Playbooks</a>
        <li> <a [routerLink]="['/servers']" routerLinkActive='active'>Servers</a>
        <li> <a [routerLink]="['/executions']" routerLinkActive='active'>Executions</a>
        <li> <a [routerLink]="['/admin']" routerLinkActive='active'>Users Management</a>

        <li class='pull-right'>{{this.getLoggedUserName()}}
          <button (click)='auth.logout()' class='btn btn-sm'>Log out</button>
      </ul>
    </navigation>
  </div>
</div>

<router-outlet></router-outlet>
`
})

export class AppComponent {
  constructor(private auth: AuthService) {
    auth.getLoggedUser();
  }

  getLoggedUserName() {
    var loggedUser = this.auth.loggedUser;
    return loggedUser && loggedUser.data ?
      loggedUser.data.full_name + ' (' + loggedUser.data.login + ')' : '';
  }
}