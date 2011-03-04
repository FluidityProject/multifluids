!    Copyright (C) 2006 Imperial College London and others.
!    
!    Please see the AUTHORS file in the main source directory for a full list
!    of copyright holders.
!
!    Prof. C Pain
!    Applied Modelling and Computation Group
!    Department of Earth Science and Engineering
!    Imperial College London
!
!    amcgsoftware@imperial.ac.uk
!    
!    This library is free software; you can redistribute it and/or
!    modify it under the terms of the GNU Lesser General Public
!    License as published by the Free Software Foundation,
!    version 2.1 of the License.
!
!    This library is distributed in the hope that it will be useful,
!    but WITHOUT ANY WARRANTY; without even the implied arranty of
!    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
!    Lesser General Public License for more details.
!
!    You should have received a copy of the GNU Lesser General Public
!    License along with this library; if not, write to the Free Software
!    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
!    USA

#include "fdebug.h"

module radiation_check_options_module

   !!< This module contains procedures that check the options associated solely with the radiation model

   use futils
   use global_parameters, only : OPTION_PATH_LEN
   use spud

   implicit none
   
   private 

   public :: radiation_check_options

contains

   ! --------------------------------------------------------------------------

   subroutine radiation_check_options() 
   
      !!< Check the options solely associted with the radiation model

      integer :: np 
      character(len=OPTION_PATH_LEN) :: np_radmat_option_path   
                           
      np_loop: do np = 1,option_count("radiation/neutral_particle")
    
         ! - 1 needed as options count from 0
         np_radmat_option_path = "/radiation/neutral_particle["//int2str(np - 1)//"]" 
         
         call radiation_check_options_neutral_particle(trim(np_radmat_option_path))
                           
      end do np_loop
                  
   end subroutine radiation_check_options

   ! --------------------------------------------------------------------------

   subroutine radiation_check_options_neutral_particle(np_radmat_option_path) 
   
      !!< Check the options solely associted with the radiation model for this
      !!< particular neutral particle object given by the option path

      character(len=*), intent(in) :: np_radmat_option_path   
      
      
      
      
   end subroutine radiation_check_options_neutral_particle

   ! --------------------------------------------------------------------------

end module radiation_check_options_module