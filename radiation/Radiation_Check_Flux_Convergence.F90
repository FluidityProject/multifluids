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

module radiation_check_flux_convergence
   
   use futils
   use global_parameters, only : OPTION_PATH_LEN
   use spud
   use fields

   use radiation_particle_data_type
   use radiation_extract_flux_field
   use radiation_energy_group_set_tools

   implicit none
   
   private 

   public ::check_particle_flux_convergence 

contains

   ! --------------------------------------------------------------------------

   subroutine check_particle_flux_convergence(particle, &
                                              flux_tolerance_absolute, &
                                              flux_converged)  
      
      !!< Check the particle flux convergence for all energy groups 
      !!< via the L Infinity difference norm

      type(particle_type), intent(in) :: particle      
      real, intent(in) :: flux_tolerance_absolute
      logical, intent(out) :: flux_converged          
      
      ! local variable
      integer :: g
      integer :: number_of_energy_groups        
      real :: difference
      real :: max_abs_difference_flux
      type(scalar_field), pointer :: particle_flux 
      type(scalar_field), pointer :: particle_flux_iter
      
      max_abs_difference_flux = 0.0
      
      ! find the number of energy groups
      call find_total_number_energy_groups(trim(particle%option_path), &
                                           number_of_energy_groups)
            
      group_loop: do g = 1,number_of_energy_groups
         
         call extract_flux_group_g(particle, &
                                   g, &  
                                   particle_flux = particle_flux, &
                                   particle_flux_iter = particle_flux_iter)
         
         ! use generic fields operation to find the L_Infinity norm of the difference
         call field_con_stats(particle_flux, &
                              particle_flux_iter, &
                              difference)
         
         ! find the max difference over all energy groups
         max_abs_difference_flux = max(max_abs_difference_flux,difference)
                           
      end do group_loop

      check_flux: if (max_abs_difference_flux < flux_tolerance_absolute) then
               
         flux_converged = .true.
               
      else check_flux
               
         flux_converged = .false.
                                                      
      end if check_flux
      
      ewrite(1,*) 'max_abs_difference_flux,flux_converged: ',max_abs_difference_flux,flux_converged
      
   end subroutine check_particle_flux_convergence  

   ! --------------------------------------------------------------------------

end module radiation_check_flux_convergence
